import PropTypes from 'prop-types';
import './UserForm.css';

function UserForm({ formElement }) {
  return (
    <div className="user-form">
      <div className="user-form__card">{formElement}</div>
    </div>
  );
}

UserForm.propTypes = {
  formElement: PropTypes.element.isRequired
};

export default UserForm;
