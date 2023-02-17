import UserForm from '../components/UserForm';
import './Login.css';

function Login() {
  const loginJsx = (
    <div className="login">
      <h1 className="login__logo">chatter</h1>
      <h2 className="login__main-header">Welcome!</h2>
      <p className="login__subheader">
        Chat with friends and famiily in the comfort of your browser!
      </p>
      <form className="login__form">
        <div className="login__form-input">
          <label className="login__form-label" htmlFor="email">
            Email<span className="login__required-text">*</span>
          </label>
          <input
            className="login__form-text-box"
            type="text"
            id="email"
            name="email"
            autoComplete="off"
          />
        </div>
        <div className="login__form-input">
          <label className="login__form-label" htmlFor="pwd">
            Password<span className="login__required-text">*</span>
          </label>
          <input className="login__form-text-box" type="password" id="pwd" name="pwd" />
        </div>
        <button className="login_form-button" type="submit">
          Log In
        </button>
      </form>
    </div>
  );

  return <UserForm formElement={loginJsx} />;
}

export default Login;
