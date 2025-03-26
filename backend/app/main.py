import os
import uuid
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from .game import GameState, Card, CardType, CardSuit, CardRank
from .ai_player import AIPlayer
import asyncio
import secrets
import json
from datetime import datetime, timedelta

# 创建 FastAPI 应用
app = FastAPI(title="掼蛋游戏 API")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储所有活跃的游戏房间
active_games = {}

# 存储所有连接的客户端
connected_clients = {}

# 邀请链接管理
invite_links = {}

def generate_invite_link(room_id: str) -> str:
    """生成邀请链接"""
    token = secrets.token_urlsafe(16)
    invite_links[token] = {
        "room_id": room_id,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    return token

def validate_invite_link(token: str) -> dict:
    """验证邀请链接"""
    if token not in invite_links:
        return None
    
    link_data = invite_links[token]
    if datetime.now() > link_data["expires_at"]:
        del invite_links[token]
        return None
    
    return link_data

@app.get("/")
async def read_root():
    return {"message": "Welcome to Guandan Game API"}

@app.get("/game/create")
async def create_game(player_name: str, mode: str = "single"):
    """
    创建一个新的游戏房间
    """
    room_id = str(uuid.uuid4())[:8]
    
    # 创建游戏实例
    game_state = GameState()
    game_state.deal_cards()
    
    # 存储游戏实例
    active_games[room_id] = {
        "game_state": game_state,
        "players": [{"id": str(uuid.uuid4())[:8], "name": player_name}],
        "mode": mode
    }
    
    player_id = active_games[room_id]["players"][0]["id"]
    
    # 如果是单人模式，添加AI玩家
    if mode == "single":
        for i in range(1, 4):
            active_games[room_id]["players"].append({
                "id": f"ai_{i}",
                "name": f"AI 玩家 {i}"
            })
    
    return {
        "roomId": room_id,
        "playerId": player_id,
        "mode": mode
    }

@app.get("/game/join/{room_id}")
async def join_game(room_id: str, player_name: str):
    """
    加入一个已存在的游戏房间
    """
    if room_id not in active_games:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = active_games[room_id]
    
    if room["mode"] != "multiplayer":
        raise HTTPException(status_code=400, detail="不能加入单人模式游戏")
    
    if len(room["players"]) >= 4:
        raise HTTPException(status_code=400, detail="房间已满")
    
    player_id = str(uuid.uuid4())[:8]
    room["players"].append({"id": player_id, "name": player_name})
    
    # 如果人数达到4人，分发卡牌
    if len(room["players"]) == 4:
        room["game_state"].deal_cards()
    
    return {
        "roomId": room_id,
        "playerId": player_id
    }

@app.get("/game/status/{room_id}")
async def get_game_status(room_id: str, player_id: Optional[str] = None):
    """
    获取游戏当前状态
    """
    if room_id not in active_games:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    room = active_games[room_id]
    game_state = room["game_state"]
    
    # 获取对应玩家视角的游戏状态
    if player_id:
        player_index = next((i for i, p in enumerate(room["players"]) if p["id"] == player_id), None)
        if player_index is None:
            raise HTTPException(status_code=404, detail="玩家不存在")
        
        # 构建玩家视角的游戏状态
        return {
            "roomId": room_id,
            "players": room["players"],
            "myIndex": player_index,
            "myHand": [str(card) for card in game_state.players_hands[player_index]],
            "currentTurn": game_state.current_player,
            "currentLevel": game_state.current_level,
            "lastPlayedCards": [str(card) for card in game_state.last_played_cards] if game_state.last_played_cards else None,
            "lastPlayedPlayer": game_state.last_played_player,
            "playerHandsCount": [len(hand) for hand in game_state.players_hands]
        }
    
    # 返回公共游戏状态信息
    return {
        "roomId": room_id,
        "players": room["players"],
        "currentLevel": game_state.current_level,
        "currentTurn": game_state.current_player,
        "lastPlayedCards": [str(card) for card in game_state.last_played_cards] if game_state.last_played_cards else None
    }

@app.websocket("/ws/{room_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str, player_id: str):
    await websocket.accept()
    
    if room_id not in active_games:
        await websocket.send_json({"error": "房间不存在"})
        await websocket.close()
        return
    
    room = active_games[room_id]
    player_index = next((i for i, p in enumerate(room["players"]) if p["id"] == player_id), None)
    
    if player_index is None:
        await websocket.send_json({"error": "玩家不存在"})
        await websocket.close()
        return
    
    # 将 WebSocket 连接与玩家关联
    connected_clients[player_id] = websocket
    
    try:
        # 发送初始游戏状态
        game_state = room["game_state"]
        await websocket.send_json({
            "type": "game_state", 
            "data": {
                "roomId": room_id,
                "players": room["players"],
                "myIndex": player_index,
                "myHand": [str(card) for card in game_state.players_hands[player_index]],
                "currentTurn": game_state.current_player,
                "currentLevel": game_state.current_level,
                "lastPlayedCards": [str(card) for card in game_state.last_played_cards] if game_state.last_played_cards else None,
                "lastPlayedPlayer": game_state.last_played_player,
                "playerHandsCount": [len(hand) for hand in game_state.players_hands]
            }
        })
        
        # 如果是单人模式并且现在是AI玩家的回合，让AI玩家行动
        if room["mode"] == "single" and game_state.current_player != player_index:
            await handle_ai_turns(room, room_id)
        
        # 监听玩家操作
        while True:
            data = await websocket.receive_json()
            
            if data["action"] == "play_cards":
                cards_str = data["cards"]
                # 将字符串转换为Card对象
                cards = []
                for card_str in cards_str:
                    suit_str = card_str[0]
                    rank_str = card_str[1:]
                    
                    # 处理大小王的特殊情况
                    if "王" in card_str:
                        suit = CardSuit.JOKER
                        rank = CardRank.JOKER_BIG if "大" in card_str else CardRank.JOKER_SMALL
                    else:
                        # 根据字符确定花色
                        if suit_str == "♠":
                            suit = CardSuit.SPADES
                        elif suit_str == "♥":
                            suit = CardSuit.HEARTS
                        elif suit_str == "♦":
                            suit = CardSuit.DIAMONDS
                        else:
                            suit = CardSuit.CLUBS
                        
                        # 确定牌点
                        rank_map = {
                            "2": CardRank.TWO,
                            "3": CardRank.THREE,
                            "4": CardRank.FOUR,
                            "5": CardRank.FIVE,
                            "6": CardRank.SIX,
                            "7": CardRank.SEVEN,
                            "8": CardRank.EIGHT,
                            "9": CardRank.NINE,
                            "10": CardRank.TEN,
                            "J": CardRank.JACK,
                            "Q": CardRank.QUEEN,
                            "K": CardRank.KING,
                            "A": CardRank.ACE
                        }
                        rank = rank_map.get(rank_str)
                    
                    if suit and rank:
                        cards.append(Card(suit, rank))
                
                # 尝试出牌
                success = game_state.play_cards(cards, player_index)
                
                if success:
                    # 广播更新后的游戏状态
                    await broadcast_game_state(room, room_id)
                    
                    # 检查游戏是否结束
                    game_result = game_state.check_game_end()
                    if game_result:
                        await broadcast_to_room(room_id, {
                            "type": "game_end",
                            "data": game_result
                        })
                        
                        # 重置游戏状态
                        game_state = GameState()
                        game_state.deal_cards()
                        room["game_state"] = game_state
                        await broadcast_game_state(room, room_id)
                    elif room["mode"] == "single" and game_state.current_player != player_index:
                        # 如果是单人模式，并且下一个玩家不是真人玩家，触发AI行动
                        await handle_ai_turns(room, room_id)
                else:
                    await websocket.send_json({"type": "error", "message": "无效的出牌"})
            
            elif data["action"] == "pass":
                success = game_state.pass_turn(player_index)
                
                if success:
                    # 广播更新后的游戏状态
                    await broadcast_game_state(room, room_id)
                    
                    # 如果是单人模式，让 AI 玩家行动
                    if room["mode"] == "single" and game_state.current_player != player_index:
                        await handle_ai_turns(room, room_id)
                else:
                    await websocket.send_json({"type": "error", "message": "现在不能过牌"})
    
    except WebSocketDisconnect:
        # 移除断开连接的客户端
        if player_id in connected_clients:
            del connected_clients[player_id]
        
        # 如果是多人模式，广播玩家离开消息
        if room["mode"] == "multiplayer":
            await broadcast_to_room(room_id, {
                "type": "player_left",
                "playerId": player_id,
                "playerName": room["players"][player_index]["name"]
            })

async def broadcast_to_room(room_id: str, message: Dict[str, Any]):
    """
    向房间内所有玩家广播消息
    """
    if room_id not in active_games:
        return
    
    room = active_games[room_id]
    
    for player in room["players"]:
        if player["id"] in connected_clients:
            await connected_clients[player["id"]].send_json(message)

async def broadcast_game_state(room: Dict, room_id: str):
    """
    向房间内所有玩家广播游戏状态
    """
    game_state = room["game_state"]
    
    for i, player in enumerate(room["players"]):
        if player["id"] in connected_clients:
            await connected_clients[player["id"]].send_json({
                "type": "game_state",
                "data": {
                    "roomId": room_id,
                    "players": room["players"],
                    "myIndex": i,
                    "myHand": [str(card) for card in game_state.players_hands[i]],
                    "currentTurn": game_state.current_player,
                    "currentLevel": game_state.current_level,
                    "lastPlayedCards": [str(card) for card in game_state.last_played_cards] if game_state.last_played_cards else None,
                    "lastPlayedPlayer": game_state.last_played_player,
                    "playerHandsCount": [len(hand) for hand in game_state.players_hands]
                }
            })

async def handle_ai_turns(room: Dict, room_id: str):
    """
    处理 AI 玩家的行动
    """
    game_state = room["game_state"]
    current_player = game_state.current_player
    
    # 循环直到轮到真人玩家或游戏结束
    while room["players"][current_player]["id"].startswith("ai_"):
        # 创建 AI 实例
        ai = AIPlayer(game_state, current_player)
        
        # 让AI思考一会
        await asyncio.sleep(1)
        
        # 获取 AI 决策
        action = ai.make_decision()
        
        if action["action"] == "play":
            # AI 出牌
            game_state.play_cards(action["cards"], current_player)
        else:
            # AI 过牌
            game_state.pass_turn(current_player)
        
        # 广播游戏状态
        await broadcast_game_state(room, room_id)
        
        # 检查游戏是否结束
        game_result = game_state.check_game_end()
        if game_result:
            await broadcast_to_room(room_id, {
                "type": "game_end",
                "data": game_result
            })
            
            # 重置游戏状态
            game_state = GameState()
            game_state.deal_cards()
            room["game_state"] = game_state
            await broadcast_game_state(room, room_id)
            return
        
        # 更新当前玩家
        current_player = game_state.current_player
        
        # 如果轮到真人玩家，结束AI回合
        if not room["players"][current_player]["id"].startswith("ai_"):
            break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 