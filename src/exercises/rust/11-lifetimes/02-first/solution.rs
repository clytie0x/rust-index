use std::io::Read;

fn first_word(text: &str) -> &str {
    text.split_whitespace().next().unwrap_or("none")
}

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    println!("{}", first_word(&input));
}
