import axios from 'axios';
import { PropTypes } from 'prop-types';
import React, { useRef, createContext } from 'react';
import jwtDecode from 'jwt-decode';

const authTokensCookieName = 'authTokens';

const AuthContext = createContext();
export default AuthContext;

export function AuthProvider({ children }) {
  const authTokens = useRef(
    localStorage.getItem(authTokensCookieName)
      ? JSON.parse(localStorage.getItem(authTokensCookieName))
      : null
  );
  const user = useRef(authTokens.current ? jwtDecode(authTokens.current.access) : null);

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

    authTokens.current = response.data;
    user.current = jwtDecode(response.data.access);
    localStorage.setItem(authTokensCookieName, JSON.stringify(response.data));

    return true;
  };

  const logoutUser = () => {
    authTokens.current = null;
    user.current = null;
    localStorage.removeItem(authTokensCookieName);
  };

  return (
    <AuthContext.Provider
      value={{
        user: user,
        authTokens: authTokens,
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
