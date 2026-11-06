use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut parts = input.split_whitespace();
    let first: i32 = parts.next().unwrap().parse().unwrap();
    match parts.next() {
        Some(text) => {
            let second: i32 = text.parse().unwrap();
            println!("{}", first + second);
        }
        None => println!("{first}"),
    }
}
