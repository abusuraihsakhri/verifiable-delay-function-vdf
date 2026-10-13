const test = require('node:test');
const assert = require('node:assert/strict');
globalThis.crypto = require('node:crypto').webcrypto;
const vdf = require('../web/vdf.js');

test('evaluation and proof match independent BigInt exponent', async () => {
  for (const t of [1, 12, 80, 512]) {
    const result = await vdf.prove('1000036000099', '5', t);
    assert.equal(BigInt(result.output), vdf.powmod(5n, 2n ** BigInt(t), 1000036000099n));
    assert.equal(BigInt(result.proof), vdf.powmod(5n, (2n ** BigInt(t)) / BigInt(result.challenge), 1000036000099n));
    assert.equal(await vdf.verify(result), true);
  }
});

test('tampering is rejected', async () => {
  const result = await vdf.prove('77', '2', 48);
  assert.equal(await vdf.verify(result), true);
  for (const field of ['output','proof','challenge','remainder','modulus','base','iterations']) {
    const modified = {...result, [field]: String(BigInt(result[field]) + 1n)};
    assert.equal(await vdf.verify(modified), false, field);
  }
});

test('input validation', async () => {
  await assert.rejects(vdf.prove('77', '7', 1), /coprime/);
  await assert.rejects(vdf.prove('77', '2', 10001), /Iterations/);
  await assert.rejects(vdf.prove('77.0', '2', 1), /decimal integer/);
});
