var btnA = document.getElementById('AA'),
      btnB = document.getElementById('AB'),
      btnC = document.getElementById('AC'),
      btnD = document.getElementById('AD');

      /**
       * @param {string} name 이름 넣어보쇼
       */ 
function btnClick(name) {
    console.log(name,"is clicked")
}

btnA.addEventListener('click', btnClick("A"));
btnB.addEventListener('click', btnClick("B"));
btnC.addEventListener('click', btnClick("C"));
btnD.addEventListener('click', btnClick("D"));