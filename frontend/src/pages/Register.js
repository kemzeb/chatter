import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import UserForm from '../components/UserForm';
import { baseUrl } from '../utils/consts';
import '../components/UserForm.css';

function Register() {
  const navigate = useNavigate();

  const handleRegister = (e) => {
    e.preventDefault();

    axios
      .post(`${baseUrl}/api/users/auth/register/`, {
        email: e.target.email.value,
        username: e.target.username.value,
        password: e.target.password.value
      })
      .then(() => {
        alert('Account successfully registered!');
        navigate('/');
      })
      .catch((error) => {
        const data = error.response.data;

        // TODO: This information should be placed near the offending text boxes
        // rather than throwing it in a alert dialog(I say text boxes as we may
        // recieve multiple errors but we don't handle that right now).
        if (error.response.status == 400) {
          let msg = '';
          if (data.username) {
            msg = data.username.toString().replace(/,/g, ' ');
            alert('Username: ' + msg);
          } else if (data.password) {
            msg = data.password.toString().replace(/,/g, ' ');
            alert('Password: ' + msg);
          } else if (data.email) {
            msg = data.email.toString().replace(/,/g, ' ');
            alert('Email: ' + msg);
          } else {
            alert('400 bad request');
          }
        } else {
          alert(error);
        }
      });
  };

  const registerJsx = (
    <>
      <h1 className="user-form__logo">chatter</h1>
      <h2 className="user-form__main-header">Create an account</h2>
      <form className="user-form__form" onSubmit={handleRegister}>
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
          <label className="user-form__label" htmlFor="password">
            Password<span className="user-form__required-text">*</span>
          </label>
          <input className="user-form__text-box" type="password" id="password" name="password" />
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
