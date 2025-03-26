import { createStore } from 'vuex'

export default createStore({
  state: {
    player: {
      id: null,
      name: ''
    },
    room: {
      id: null,
      mode: ''
    },
    game: {
      currentTurn: 0,
      currentLevel: 2,
      lastPlayedCards: null,
      myHand: [],
      playerHandsCount: []
    }
  },
  mutations: {
    setPlayer(state, player) {
      state.player = player
    },
    setRoom(state, room) {
      state.room = room
    },
    updateGame(state, gameState) {
      state.game = { ...state.game, ...gameState }
    },
    clearState(state) {
      state.player = { id: null, name: '' }
      state.room = { id: null, mode: '' }
      state.game = {
        currentTurn: 0,
        currentLevel: 2,
        lastPlayedCards: null,
        myHand: [],
        playerHandsCount: []
      }
    }
  },
  actions: {
    initializePlayer({ commit }, { id, name }) {
      commit('setPlayer', { id, name })
    },
    joinRoom({ commit }, { id, mode }) {
      commit('setRoom', { id, mode })
    },
    updateGameState({ commit }, gameState) {
      commit('updateGame', gameState)
    },
    resetState({ commit }) {
      commit('clearState')
    }
  },
  getters: {
    isMyTurn: (state) => {
      return state.game.currentTurn === state.player.myIndex
    },
    canPass: (state) => {
      return state.game.lastPlayedCards !== null
    }
  }
}) 