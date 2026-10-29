// Chirpstack v4: Device profile > Codec > JavaScript functions
// payload 4 ไบต์: temp*100 (int16 BE) + humidity*100 (uint16 BE)
function decodeUplink(input) {
  var b = input.bytes;
  if (b.length < 4) {
    return { errors: ["payload too short"] };
  }
  var t = ((b[0] << 8) | b[1]) << 16 >> 16; // แปลงเป็น signed 16-bit
  var h = (b[2] << 8) | b[3];
  return {
    data: {
      temperature: t / 100,
      humidity: h / 100,
    },
  };
}
