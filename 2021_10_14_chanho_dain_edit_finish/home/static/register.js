/* 등록 팝업 */
function showPopup(hasFilter) {
   const popup = document.querySelector('#popup');

  if (hasFilter) {
     popup.classList.add('has-filter');
  } else {
     popup.classList.remove('has-filter');
  }

  popup.classList.remove('hide');
}

function closePopup() {
   const popup = document.querySelector('#popup');
  popup.classList.add('hide');
}

/* 조회 팝업 */

function closePopupCheck() {
   const popupCheck = document.querySelector('#popupCheck');
  popupCheck.classList.add('hide');
}

/* 체크박스 하나만 선택 */
function checkOnlyOneRegister(element) {
  const checkboxes
      = document.getElementsByName("ckbSelect");

  checkboxes.forEach((cb) => {
      cb.checked = false;
  })

  element.checked = true;
}