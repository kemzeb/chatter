import axios from 'axios';
import { PropTypes } from 'prop-types';
import React, { useState, createContext } from 'react';
import jwtDecode from 'jwt-decode';

const authTokensCookieName = 'authTokens';

const AuthContext = createContext();
export default AuthContext;

export function AuthProvider({ children }) {
  const [authTokens, setAuthTokens] = useState(() =>
    localStorage.getItem(authTokensCookieName)
      ? JSON.parse(localStorage.getItem(authTokensCookieName))
      : null
  );
  const [user, setUser] = useState(() => (authTokens ? jwtDecode(authTokens.access) : null));

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

    setAuthTokens(response.data);
    setUser(jwtDecode(response.data.access));
    localStorage.setItem(authTokensCookieName, JSON.stringify(response.data));

    return true;
  };

  const logoutUser = () => {
    setAuthTokens(null);
    setUser(null);
    localStorage.removeItem(authTokensCookieName);
  };

  return (
    <AuthContext.Provider
      value={{
        user: user,
        authTokens: authTokens,
        setUser: setUser,
        setAuthTokens: setAuthTokens,
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
