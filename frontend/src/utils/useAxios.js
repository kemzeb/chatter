import axios from 'axios';
import jwtDecode from 'jwt-decode';
import { useContext } from 'react';
import AuthContext from './AuthContext';

function useAxios() {
  const { authTokens, setUser, setAuthTokens } = useContext(AuthContext);

  const axiosInstance = axios.create({
    baseURL: window.location.protocol + '//' + window.location.host,
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
          const refreshResponse = await axiosInstance.post(`/api/users/auth/login/refresh/`, {
            refresh: authTokens.refresh
          });
          // FIXME: Handle failure to refresh JWT (maybe just navigate back to login).
          localStorage.setItem('authTokens', JSON.stringify(refreshResponse.data));
          setAuthTokens((prevTokens) => {
            return {
              access: refreshResponse.data['access'],
              refresh: prevTokens['refresh']
            };
          });
          setUser(jwtDecode(refreshResponse.data.access));
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
