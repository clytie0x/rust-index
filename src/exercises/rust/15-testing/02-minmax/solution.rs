use std::io::Read;

fn smaller(a: i32, b: i32) -> i32 {
    if a <= b { a } else { b }
}

fn larger(a: i32, b: i32) -> i32 {
    if a >= b { a } else { b }
}

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut parts = input.split_whitespace();
    let a: i32 = parts.next().unwrap().parse().unwrap();
    let b: i32 = parts.next().unwrap().parse().unwrap();
    let c: i32 = parts.next().unwrap().parse().unwrap();
    let low = smaller(smaller(a, b), c);
    let high = larger(larger(a, b), c);
    println!("min = {low}");
    println!("max = {high}");
}
