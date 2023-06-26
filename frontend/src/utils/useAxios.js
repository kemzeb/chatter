import axios from 'axios';
import jwtDecode from 'jwt-decode';
import { useContext } from 'react';
import AuthContext from './AuthContext';
import { redirect } from 'react-router-dom';

function useAxios() {
  const { authTokens, user } = useContext(AuthContext);

  const axiosInstance = axios.create({
    baseURL: window.location.protocol + '//' + window.location.host,
    headers: { Authorization: `Bearer ${authTokens.current.access}` }
  });

  axiosInstance.interceptors.response.use(
    async (resp) => {
      return resp;
    },
    async (error) => {
      if (error.response) {
        const originalRequest = error.config;

        if (originalRequest._retry) return Promise.reject(error);
        originalRequest._retry = true;

        if (error.response.status == 401) {
          const refreshResponse = await axiosInstance
            .post(`/api/users/auth/login/refresh/`, {
              refresh: authTokens.current.refresh
            })
            .catch(() => {
              redirect('/');
            });

          const access = refreshResponse.data['access'];

          localStorage.setItem(
            'authTokens',
            JSON.stringify({
              access: access,
              refresh: authTokens.current.refresh
            })
          );
          authTokens.current = {
            access: access,
            refresh: authTokens.current.refresh
          };
          user.current = jwtDecode(access);
          originalRequest['headers'] = { Authorization: `Bearer ${refreshResponse.data.access}` };

          return axiosInstance(originalRequest);
        }
      }

      return Promise.reject(error);
    }
  );

  return axiosInstance;
}

export default useAxios;
