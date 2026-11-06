use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut nums = input.split_whitespace();
    let n: usize = nums.next().unwrap().parse().unwrap();
    let mut best: i32 = nums.next().unwrap().parse().unwrap();
    for _ in 1..n {
        let x: i32 = nums.next().unwrap().parse().unwrap();
        if x > best {
            best = x;
        }
    }
    println!("{best}");
}
