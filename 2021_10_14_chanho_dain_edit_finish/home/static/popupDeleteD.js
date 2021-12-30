function showPopupDeleteD(hasFilter) {
	const popup = document.querySelector('#popupDeleteD');
  
  if (hasFilter) {
  	popup.classList.add('has-filter');
  } else {
  	popup.classList.remove('has-filter');
  }
  
  popup.classList.remove('hide');
}

function closePopupDeleteD() {
	const popup = document.querySelector('#popupDeleteD');
  popup.classList.add('hide');
}
