console.log('reset')
$(function () {
  $('#forgotPasswordForm').submit(reset);
});

function reset(e) {
  let form = $(this);
  e.preventDefault();
  $.ajax({
    url: '/api/v1/auth/password/reset/',
    type: 'post',
    data: form.serialize(),
    success: resetSuccessHandler,
    error: resetErrorHandler,
  })
}

function resetSuccessHandler(data) {
  console.log('success', data)
}

function resetErrorHandler(data) {
  console.log('error', data)
}