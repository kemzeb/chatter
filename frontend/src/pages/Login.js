import { Link } from 'react-router-dom';
import UserForm from '../components/UserForm';
import '../components/UserForm.css';

function Login() {
  const loginJsx = (
    <>
      <h1 className="user-form__logo">chatter</h1>
      <h2 className="user-form__main-header">Welcome!</h2>
      <p className="user-form__subheader">
        Chat with friends and family in the comfort of your browser!
      </p>
      <form className="user-form__form">
        <div className="user-form__input-text">
          <label className="user-form__label" htmlFor="email">
            Email<span className="user-form__required-text">*</span>
          </label>
          <input
            className="user-form__text-box"
            type="text"
            id="email"
            name="email"
            autoComplete="off"
          />
        </div>
        <div className="user-form__input-text">
          <label className="user-form__label" htmlFor="pwd">
            Password<span className="user-form__required-text">*</span>
          </label>
          <input className="user-form__text-box" type="password" id="pwd" name="pwd" />
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
