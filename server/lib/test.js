var io = require("socket.io-client");
var dataSocketConfig = require("../configs/datasocket");
const { ecg } = require("./ecg");

module.exports = function (iso) {
  const ecgConfig = dataSocketConfig.ecg;

  var baseSocket = io("http://192.168.1.100:3000" + ecgConfig.namespace);

  // simulated ecg
  let index = 0;
  setInterval(() => {
    if (index >= ecg.length) {
      index = 0;
    }
    baseSocket.emit(ecgConfig.rawDataReceived, `1,${ecg[index]}`);
    index++;
  }, 30);

  // setInterval(() => {
  //   f1 = 0.5;
  //   var t1 = Date.now() / 1000;
  //   var v1 = Math.round(512 * Math.sin(2 * Math.PI * f1 * t1)) + 512;
  //   baseSocket.emit(ecgConfig.rawDataReceived, `1,${v1}`);
  // }, 20);
};
