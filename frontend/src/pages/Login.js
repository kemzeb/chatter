import { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import UserForm from '../components/UserForm';
import '../components/UserForm.css';
import AuthContext from '../utils/AuthContext';

function Login() {
  const { loginUser } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    loginUser(e).then((loginWasSuccessful) => {
      console.log(loginWasSuccessful);
      if (loginWasSuccessful) {
        navigate('/dashboard');
      } else {
        alert('Username or password is invalid.');
      }
    });
  };

  const loginJsx = (
    <>
      <h1 className="user-form__logo">chatter</h1>
      <h2 className="user-form__main-header">Welcome!</h2>
      <p className="user-form__subheader">
        Chat with friends and family in the comfort of your browser!
      </p>
      <form className="user-form__form" onSubmit={handleLogin}>
        <div className="user-form__input-text">
          <label className="user-form__label" htmlFor="username">
            Username<span className="user-form__required-text">*</span>
          </label>
          <input
            className="user-form__text-box"
            type="text"
            id="username"
            name="username"
            autoComplete="off"
          />
        </div>
        <div className="user-form__input-text">
          <label className="user-form__label" htmlFor="password">
            Password<span className="user-form__required-text">*</span>
          </label>
          <input className="user-form__text-box" type="password" id="password" name="password" />
        </div>
        <button className="user-form__button" type="submit">
          Log In
        </button>
      </form>
      <div className="user-form__alternative-link-text">
        Need an account?{' '}
        <Link className="user-form__alternative-link" to="/register">
          Register
        </Link>
      </div>
    </>
  );

  return <UserForm formElement={loginJsx} />;
}

export default Login;
