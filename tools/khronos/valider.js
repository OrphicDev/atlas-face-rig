// Appelant du validateur Khronos glTF. Il ne juge rien : il rend le JSON du
// validateur tel quel, pour que rien ne soit reinterprete en chemin.
const fs = require('fs');
const path = require('path');
const validator = require(process.env.GLTF_VALIDATOR_PATH || 'gltf-validator');

const fichier = process.argv[2];
if (!fichier) { console.error('usage: node valider.js <fichier.glb>'); process.exit(2); }
const octets = new Uint8Array(fs.readFileSync(fichier));

validator.validateBytes(octets, {
  uri: path.basename(fichier),
  maxIssues: 1000,
  externalResourceFunction: (uri) =>
    new Promise((resolve, reject) =>
      fs.readFile(path.resolve(path.dirname(fichier), decodeURIComponent(uri)),
        (e, d) => e ? reject(e.toString()) : resolve(new Uint8Array(d))))
}).then((rapport) => {
  process.stdout.write(JSON.stringify(rapport));
}).catch((e) => {
  console.error('VALIDATEUR EN ERREUR :', e);
  process.exit(1);
});
