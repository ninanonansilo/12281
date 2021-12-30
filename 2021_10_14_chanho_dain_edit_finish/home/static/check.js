/* 조회 팝업 */
/*
function showPopupCheck(hasFilter) {
	const popupCheck = document.querySelector('#popupCheck');
  
  if (hasFilter) {
  	popupCheck.classList.add('has-filter');
  } else {
  	popupCheck.classList.remove('has-filter');
  }
  
  popupCheck.classList.remove('hide');
}
*/
function closePopupCheck() {
	const popupCheck = document.querySelector('#popupCheck');
  popupCheck.classList.add('hide');
}