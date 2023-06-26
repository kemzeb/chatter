import { Navigate, useLocation } from 'react-router';
import PropTypes from 'prop-types';
import { useContext } from 'react';
import AuthContext from './AuthContext';

function RequireAuth({ children }) {
  const { user } = useContext(AuthContext);
  const location = useLocation();

  return user.current ? children : <Navigate to="/" state={{ from: location }} />;
}

RequireAuth.propTypes = {
  children: PropTypes.element
};

export default RequireAuth;
