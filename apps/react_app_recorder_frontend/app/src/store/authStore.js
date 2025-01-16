import { create } from 'zustand';

const useAuthStore = create((set) => ({
  token: null,
  user: null,
  setToken: (token) => set({ token }),
  setUser: (user) => set({ user }),
  logout: () => set({ token: null, user: null }), // Reset token and user on logout
}));

export default useAuthStore;
