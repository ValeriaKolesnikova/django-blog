$(function () {
    $('#resetConfirmForm').submit(reset);
  });
  
  function reset(e) {
    let form = $(this);
    e.preventDefault();
    const urlParams = new URLSearchParams (window.location.search)
    const data = {
        "uid": urlParams.get('uid'),
        "token": urlParams.get('token'),
        "password_1": $('input[name=password_1]').val(),
        "password_2": $('input[name=password_2]').val(),
      }
    $.ajax({
      url: '/api/v1/auth/password/reset/confirm/',
      type: 'post',
      data: data,
      success: resetSuccessHandler,
      error: resetErrorHandler,
    })
    console.log('reset')
  }
  
  function resetSuccessHandler(data) {
    console.log('success', data)
  }
  
  function resetErrorHandler(data) {
    console.log('error', data)
  }