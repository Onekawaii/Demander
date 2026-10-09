export function add(a: number, b: number): number { return a + b; }
const result: number = add(2, 3);
if (result !== 5) throw new Error('unreachable');
