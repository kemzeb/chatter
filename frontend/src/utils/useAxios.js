import axios from 'axios';
import jwt_decode from 'jwt-decode';
import { useContext } from 'react';
import AuthContext from '../context/AuthContext';
import { baseUrl } from './consts';

function useAuthAxios() {
  const { authTokens, setUser, setAuthTokens } = useContext(AuthContext);

  const axiosInstance = axios.create({
    baseURL: baseUrl,
    headers: { Authorization: `Bearer ${authTokens?.access}` }
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
          const refreshResponse = await axios.post(`${baseUrl}/auth/api/login/refresh/`, {
            refresh: authTokens.refresh
          });
          localStorage.setItem('authTokens', JSON.stringify(refreshResponse.data));
          setAuthTokens(refreshResponse.data);
          setUser(jwt_decode(refreshResponse.data.access));

          originalRequest['headers'] = { Authorization: `Bearer ${refreshResponse.data.access}` };
          return axiosInstance(originalRequest);
        }
      }

      return Promise.reject(error);
    }
  );

  return axiosInstance;
}

export default useAuthAxios;
