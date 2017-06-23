function numList(eleName, max, formName) {
   var select = document.getElementById(formName).elements[eleName];
   var ele = document.createElement("option");
   ele.textContent = ' ';
   ele.value = 'none';
   select.appendChild(ele);

   for(var i = 1 ; i <= max; i++) {
       var opt = String(i);
       var ele = document.createElement("option");
       ele.textContent = opt;
       ele.value = opt;
       select.appendChild(ele);
}}

function monthList(formName) {
   var select = document.getElementById(formName).elements['month'];
   var mNums = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
   var mNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

   var ele = document.createElement("option");
   ele.textContent = ' ';
   ele.value = 'none';
   select.appendChild(ele);

   for(var i = 0 ; i < 12; i++) {
       var val = mNums[i]
       var name = mNames[i];
       var ele = document.createElement("option");
       ele.textContent = name;
       ele.value = val;
       select.appendChild(ele);
}}
