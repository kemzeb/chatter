import { useContext } from 'react';
import AuthContext from '../utils/AuthContext';

function Dashboard() {
  const { user, logoutUser } = useContext(AuthContext);
  console.log(user);
  return (
    <>
      <h1 style={{ color: 'red' }}>User Id: {user.user_id}</h1>
      <button onClick={logoutUser}>Log Out</button>
    </>
  );
}

export default Dashboard;
