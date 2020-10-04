require("dotenv").config();
var express = require("express");
var path = require("path");
var cookieParser = require("cookie-parser");
var logger = require("morgan");

var indexRouter = require("./routes/index");
var usersRouter = require("./routes/users");

var app = express();

app.use(logger("dev"));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, "public")));

app.use("/", indexRouter);
app.use("/users", usersRouter);

var dataSocketConfig = require("./configs/datasocket");

app.setSocket = function (io) {
  require("./lib/test")(io);

  const ecgConfig = dataSocketConfig.ecg;

  io.on("connection", function (socket) {
    console.log("tite - " + socket.id);
  });

  var ecgNamespace = io.of(ecgConfig.namespace);
  ecgNamespace.on("connection", function (socket) {
    console.log(`SocketIO - Connected socketId: ${socket.id}`);

    socket.on(ecgConfig.rawDataReceived, function (data) {
      // Data from nodemcu is received
      console.log(data);

      // send data to client socket (mobile app)
      io.of(ecgConfig.namespace).emit(ecgConfig.mobileDataSent, data);
    });
  });
};

module.exports = app;
