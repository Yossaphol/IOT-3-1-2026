// Chirpstack v4: Device profile > Codec > JavaScript functions
// payload 3 ไบต์ จากโมดูล LDR บน Arduino
//   byte 0-1 : ค่าดิบจากขา AO (uint16 big-endian, 0-1023) ยิ่งสว่าง ค่ายิ่งน้อย
//   byte 2   : ขา DO (1 = มืด, 0 = สว่าง)
function decodeUplink(input) {
  var b = input.bytes;
  if (b.length < 2) {
    return { errors: ["payload too short"] };
  }
  var raw = (b[0] << 8) | b[1];
  var data = {
    light_raw: raw,
    light: Math.round(((1023 - raw) / 1023) * 1000) / 10, // 0-100 % ยิ่งสว่างยิ่งมาก
  };
  if (b.length >= 3) {
    data.dark = b[2] === 1;
  }
  return { data: data };
}
