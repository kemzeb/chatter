import axios from 'axios';
import { useCallback, useContext } from 'react';
import AuthContext from './AuthContext';
import { useNavigate } from 'react-router-dom';

let isRefreshing = false;
let refreshSubscribers = [];

function useAxiosProtected() {
  const { getAuthTokens, storeAuthTokens, logOutUser } = useContext(AuthContext);
  const tokens = getAuthTokens();
  const navigate = useNavigate();

  if (!tokens) navigate('/');

  const axiosInstance = axios.create({
    baseURL: window.location.protocol + '//' + window.location.host,
    headers: { Authorization: `Bearer ${tokens.access}` }
  });

  const refreshAccessToken = useCallback(() =>
    axiosInstance
      .post(`/api/users/auth/login/refresh/`, {
        refresh: tokens.refresh
      })
      .then((response) => {
        const newAccess = response.data['access'];
        storeAuthTokens(newAccess, tokens.refresh);
        return newAccess;
      })
      .catch(() => {
        logOutUser();
        navigate('/');
      })
  );

  axiosInstance.interceptors.response.use(
    (resp) => resp,
    (error) => {
      const originalRequest = error.config;

      if (error.response.status == 401 && !originalRequest._retry) {
        if (isRefreshing) {
          return new Promise((resolve) => {
            // Currently refreshing, subscribe this request as a callback so that it may
            // be serviced when we get a valid access token.
            subscribeTokenRefresh((accessToken) => {
              originalRequest.headers.Authorization = `Bearer ${accessToken}`;
              resolve(axiosInstance(originalRequest));
            });
          });
        }

        originalRequest._retry = true;
        isRefreshing = true;

        return new Promise((resolve, reject) => {
          refreshAccessToken()
            .then((accessToken) => {
              originalRequest.headers.Authorization = `Bearer ${accessToken}`;

              // Process the original request.
              resolve(axiosInstance(originalRequest));

              // Notify other pending requests of the valid access token.
              publishTokenRefresh(accessToken);
            })
            .catch((error) => reject(error))
            .finally(() => {
              isRefreshing = false;
            });
        });
      }

      return Promise.reject(error);
    }
  );

  return axiosInstance;
}

function subscribeTokenRefresh(callback) {
  refreshSubscribers.push(callback);
}

function publishTokenRefresh(accessToken) {
  refreshSubscribers.forEach((callback) => callback(accessToken));
  refreshSubscribers = [];
}

export default useAxiosProtected;
