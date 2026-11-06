use std::io::Read;

fn longer<'a>(a: &'a str, b: &'a str) -> &'a str {
    if a.len() >= b.len() { a } else { b }
}

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut parts = input.split_whitespace();
    let a = parts.next().unwrap();
    let b = parts.next().unwrap();
    println!("{}", longer(a, b));
}
