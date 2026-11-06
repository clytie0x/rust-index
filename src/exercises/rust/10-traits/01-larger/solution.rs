use std::io::Read;

fn larger<T: PartialOrd>(a: T, b: T) -> T {
    if a >= b { a } else { b }
}

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut parts = input.split_whitespace();
    let a: i32 = parts.next().unwrap().parse().unwrap();
    let b: i32 = parts.next().unwrap().parse().unwrap();
    println!("{}", larger(a, b));
}
