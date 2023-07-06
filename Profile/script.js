var saveEl = document.getElementById("save-btn");

function upload() {
  var input = document.querySelector("input[type=file]");
  var reader = new FileReader();

  reader.onloadend = function () {
    var avatar = document.querySelector(".avatar");
    avatar.src = reader.result;
  };

  reader.readAsDataURL(input.files[0]);
}

document.getElementById('phone').addEventListener('input', function(e) {
  this.value = this.value.replace(/[^0-9]/g, ''); // Remove non-numeric characters
});

// _______________________________
//NAME INPUT

var app = angular.module("profileText", []);
app.controller("myCtrl", function ($scope) {
  $scope.firstName = "Andrew";
  $scope.lastName = "Freeman";
  $scope.userTag = "freedomAF";
  $scope.bio =
    "I am a freedom loving freedom type of free person who enjoys doing free things in my free time.";
});

// _______________________________
//Cover Photo Changer
function coverphotochanger_bridge() {
  document.getElementById("coverPicture").src =
    "https://live.staticflickr.com/7291/11111496415_1cf18d1170.jpg";

  saveEl.className = "save-btn";
  document.getElementById("save-btn").innerHTML = "SAVE";
}

function coverphotochanger_city() {
  document.getElementById("coverPicture").src =
    "https://live.staticflickr.com/65535/49375360081_1d9a6bc21a.jpg";

  saveEl.className = "save-btn";
  document.getElementById("save-btn").innerHTML = "SAVE";
}

function coverphotochanger_logs() {
  document.getElementById("coverPicture").src =
    "https://live.staticflickr.com/3826/10653925834_f85c32e8b2.jpg";

  saveEl.className = "save-btn";
  document.getElementById("save-btn").innerHTML = "SAVE";
}

function coverphotochanger_plant() {
  document.getElementById("coverPicture").src =
    "https://live.staticflickr.com/65535/49375360241_2f97122d3a.jpg";

  saveEl.className = "save-btn";
  document.getElementById("save-btn").innerHTML = "SAVE";
}

function coverphotochanger_wall() {
  document.getElementById("coverPicture").src =
    "https://live.staticflickr.com/3702/11639642236_c3465e1a9d.jpg";

  saveEl.className = "save-btn";
  document.getElementById("save-btn").innerHTML = "SAVE";
}

function coverphotochanger_shoreline() {
  document.getElementById("coverPicture").src =
    "https://live.staticflickr.com/65535/49375564862_3f94621547.jpg";

  saveEl.className = "save-btn";
  document.getElementById("save-btn").innerHTML = "SAVE";
}

// _______________________________
//needs save onclick
function needssave() {
  saveEl.className = "save-btn";
  document.getElementById("save-btn").innerHTML = "SAVE";
}

// _______________________________
//Save button profile
function saveProfileEdit() {
  var saveEl = document.getElementById("save-btn");
  saveEl.className = "saved";
  document.getElementById("save-btn").innerHTML = "SAVED ✓";
}

// https://codepen.io/duketeam/pen/zKvJvN
//https://www.dukelearntoprogram.com/course1/common/js/image/SimpleImage.js

//php image upload tutorial
//https://www.youtube.com/watch?v=dvRRAWsA9JU

//CITY FOG
// <img src="https://live.staticflickr.com/65535/49375360081_1d9a6bc21a.jpg">

//gg bridge fog
//<img src="https://live.staticflickr.com/7291/11111496415_1cf18d1170.jpg">

//wood
//  <img src="https://live.staticflickr.com/3826/10653925834_f85c32e8b2.jpg">

//plant
// <img src="https://live.staticflickr.com/65535/49375360241_2f97122d3a.jpg">

//color mural
// <img src="https://live.staticflickr.com/3702/11639642236_c3465e1a9d.jpg">

//kauai shoreline
//<img src="https://live.staticflickr.com/65535/49375564862_3f94621547.jpg">

//sutro tower fog
// <img src="https://live.staticflickr.com/65535/49374907638_57edd9dded.jpg">

//https://codepen.io/havardob/pen/qBXZPRE
