use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    for word in input.split_whitespace() {
        println!("{}", word.len());
    }
}
