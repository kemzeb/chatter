import PropTypes from 'prop-types';
import { Dialog, DialogTitle } from '@mui/material';

function BaseFormDialog({ open, title, handleClose, component }) {
  return (
    <>
      <Dialog disablePortal open={open} onClose={handleClose}>
        <DialogTitle>{title}</DialogTitle>
        {component}
      </Dialog>
    </>
  );
}

BaseFormDialog.propTypes = {
  open: PropTypes.bool.isRequired,
  title: PropTypes.string.isRequired,
  handleClose: PropTypes.func.isRequired,
  component: PropTypes.element.isRequired
};

export default BaseFormDialog;
