function showPopupSend(hasFilter) {
	const popup = document.querySelector('#popupSend');
  
  if (hasFilter) {
  	popup.classList.add('has-filter');
  } else {
  	popup.classList.remove('has-filter');
  }
  
  popup.classList.remove('hide');
}

function closePopupSend() {
	const popup = document.querySelector('#popupSend');
  popup.classList.add('hide');
}