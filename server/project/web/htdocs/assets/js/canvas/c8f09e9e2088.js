// Binaları oluştur
const builds = [
    new Build(
        250,
        525,
        200,
        200,
        new Bina(5, "white", "red", "A Blok")),
    new Build(
        250,
        125,
        200,
        200,
        new Bina(5, "white", "red", "B Blok")),
    new Build(
        650,
        125,
        200,
        200,
        new Bina(5, "white", "red", "C Blok")),
    new Build(
        1100,
        125,
        200,
        200,
        new Bina(5, "white", "red", "D Blok")),
    new Build(
        640,
        525,
        250,
        200,
        new Bina(5, "green", "black", "Futbol Sahası")),
    new Build(
        955,
        525,
        150,
        175,
        new Bina(5, "yellow", "black", "Park")),
    new Build(
        1245,
        525,
        250,
        100,
        new Bina(5, "blue", "white", "Havuz")),
    new Build(
        465,
        525,
        130,
        300,
        new Bina(5, "orange", "black", "Acil Çıkış")),
    new Build(
        1125,
        525,
        100,
        300,
        new Bina(5, "orange", "black", "Site Girişi")),
    new Build(
        180,
        375,
        1150,
        100,
        new Bina(5, "orange", "black", "Yol")),
];

// Vanaları oluştur
const devices = {
    "1": new Device(135, 540, [
            new Slave(40, 560, 98, 3),
            new Slave(40, 55, 3, 760)
        ]),
    "2": new Device(195, 540, [
            new Slave(215, 507, 703, 3),
            new Slave(915, 510, 3, 250),
            new Slave(215, 507, 3, 36)
        ]),
    "3": new Device(165, 590, [
            new Slave(185, 772, 252, 3),
            new Slave(185, 639, 3, 135)
        ]),
    "5": new Device(215, 70, [
            new Slave(180, 90, 38, 3),
            new Slave(180, 92, 3, 250)
        ]),
    "7": new Device(270, 70, [
            new Slave(315, 91, 11, 3),
            new Slave(325, 33, 3, 60),
            new Slave(65, 30, 1450, 3)
        ]),
    "11": new Device(445, 70, [
            new Slave(492, 92, 33, 3),
            new Slave(522, 95, 3, 250)
        ]),
    "13": new Device(625, 75, [
            new Slave(593, 94, 34, 3),
            new Slave(593, 95, 3, 250)
        ]),
    "15": new Device(830, 75, [
            new Slave(875, 94, 35, 3),
            new Slave(907, 94, 3, 250)
        ]),
    "19": new Device(1047, 75, [
            new Slave(1015, 94, 35, 3),
            new Slave(1015, 94, 3, 250)
        ]),
    "21": new Device(1300, 75, [
            new Slave(1380, 94, 3, 250),
            new Slave(1347, 94, 35, 3)
        ]),
};

const canvasObj = new Canvas();
canvasObj.builds = builds;
canvasObj.devices = devices;

const lastStatus = (packet) => {
    console.log(`Cihazın son verileri: ${packet}`);
    var obj = JSON.parse(packet);
    // [{"id"=5, "value"=true}, {"id"=10, "value"=true}]

    for (const [key, data] of Object.entries(obj.pins)) {

 
        _dev = devices[key]
        if (typeof _dev === "undefined"){
            continue
        }
        _dev.value = data["value"];

    }
    canvasObj.draw();
};

const serverConnected = () => {
    console.log("sunucuya bağlandı");
};

const serverDisconnected = () => {
    console.log("sunucudan bağlantı koptu");
};

const onConnected = (client_id) => {
    console.log(`Cihaz bağlandı: ${client_id}`);
};

const onDisconnected = (client_id) => {
    console.log(`Cihazın bağlatı koptu: ${client_id}`);
};

const onMessage = (packet) => {
    console.log(`Cihazın gelen: ${packet}`);

    var obj = JSON.parse(packet);
    // [{"id"=5, "value"=true}, {"id"=10, "value"=true}]

    for (const [key, data] of Object.entries(obj.pins)) {

 
            _dev = devices[key]
            if (typeof _dev === "undefined"){
                continue
            }
            _dev.value = data["value"];

    }
    canvasObj.draw();

};

/*
for (const [key, device] of Object.entries(devices)) {
    device.draw();
}
*/

canvasObj.draw();
