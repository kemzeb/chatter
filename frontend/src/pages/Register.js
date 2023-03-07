import { Link } from 'react-router-dom';
import UserForm from '../components/UserForm';
import '../components/UserForm.css';

function Register() {
  const registerJsx = (
    <>
      <h1 className="user-form__logo">chatter</h1>
      <h2 className="user-form__main-header">Create an account</h2>
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
          <label className="user-form__label" htmlFor="username">
            Username<span className="user-form__required-text">*</span>
          </label>
          <input className="user-form__text-box" type="text" id="username" name="username" />
        </div>
        <div className="user-form__input-text">
          <label className="user-form__label" htmlFor="pwd">
            Password<span className="user-form__required-text">*</span>
          </label>
          <input className="user-form__text-box" type="password" id="pwd" name="pwd" />
        </div>
        <button className="user-form__button" type="submit">
          Register
        </button>
      </form>
      <div className="user-form__alternative-link-text">
        Already have an account?{' '}
        <Link className="user-form__alternative-link" to="/">
          Log In
        </Link>
      </div>
    </>
  );
  return <UserForm formElement={registerJsx} />;
}

export default Register;
