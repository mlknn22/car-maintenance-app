import type { Token, User, UserCreate } from "../types";
import { apiRequest } from "./client";

export function login(email: string, password: string): Promise<Token> {
  const form = new URLSearchParams();
  form.set("username", email);
  form.set("password", password);
  return apiRequest<Token>("/auth/login", { method: "POST", form });
}

export function register(payload: UserCreate): Promise<User> {
  return apiRequest<User>("/auth/register", { method: "POST", body: payload });
}

export function getMe(): Promise<User> {
  return apiRequest<User>("/auth/me");
}
