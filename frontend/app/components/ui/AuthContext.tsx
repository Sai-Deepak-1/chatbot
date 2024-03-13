import React, { createContext, useState, useEffect, ReactNode } from "react";
import { createClient, SupabaseClient, User } from "@supabase/supabase-js";

const supabaseUrl = "your_supabase_url";
const supabaseAnonKey = "your_supabase_anon_key";
const supabase: SupabaseClient = createClient(supabaseUrl, supabaseAnonKey);

interface AuthContextType {
  user: User | null;
  login: () => void;
  logout: () => void;
  authReady: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  login: () => {},
  logout: () => {},
  authReady: false,
});

interface AuthContextProviderProps {
  children: ReactNode;
}

export const AuthContextProvider = ({ children }: AuthContextProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [authReady, setAuthReady] = useState<boolean>(false);

  useEffect(() => {
    const session = supabase.auth.session();

    setUser(session?.user || null);
    setAuthReady(true);

    const { data: authListener } = supabase.auth.onAuthStateChange(
      (event, session) => {
        if (event === "SIGNED_IN") {
          setUser(session?.user || null);
          console.log("login event");
        } else if (event === "SIGNED_OUT") {
          setUser(null);
          console.log("logout event");
        }
      }
    );

    return () => {
      authListener?.unsubscribe();
    };
  }, []);

  const login = () => {
    supabase.auth.signIn({ provider: "google" }); // Example with Google provider
  };

  const logout = () => {
    supabase.auth.signOut();
  };

  const context: AuthContextType = { user, login, logout, authReady };

  return (
    <AuthContext.Provider value={context}>{children}</AuthContext.Provider>
  );
};

export default AuthContext;
