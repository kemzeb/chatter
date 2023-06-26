import axios from 'axios';
import { PropTypes } from 'prop-types';
import React, { createContext, useCallback } from 'react';
import jwtDecode from 'jwt-decode';

const tokensStorageName = 'authTokens';

const AuthContext = createContext();
export default AuthContext;

export function AuthProvider({ children }) {
  const getAuthTokens = useCallback(() => {
    const tokens = localStorage.getItem(tokensStorageName);
    return tokens ? JSON.parse(tokens) : null;
  });

  const getUser = useCallback(() => {
    const tokens = getAuthTokens();
    return tokens ? jwtDecode(tokens?.access) : null;
  });

  const storeAuthTokens = useCallback((access, refresh) => {
    localStorage.setItem(
      tokensStorageName,
      JSON.stringify({
        access: access,
        refresh: refresh
      })
    );
  });

  const loginUser = async (e) => {
    let status = -1;

    const response = await axios
      .post(`/api/users/auth/login/`, {
        username: e.target.username.value,
        password: e.target.password.value
      })
      .catch((error) => (status = error.response.status));

    // TODO: Find a better way to handle 401s or other errors.
    if (status != -1) return false;

    localStorage.setItem(tokensStorageName, JSON.stringify(response.data));

    return true;
  };

  const logoutUser = () => localStorage.removeItem(tokensStorageName);

  return (
    <AuthContext.Provider
      value={{
        getUser: getUser,
        getAuthTokens: getAuthTokens,
        storeAuthTokens: storeAuthTokens,
        loginUser: loginUser,
        logoutUser: logoutUser
      }}>
      {children}
    </AuthContext.Provider>
  );
}

AuthProvider.propTypes = {
  children: PropTypes.node
};
