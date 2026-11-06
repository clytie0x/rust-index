use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let mut count = 0;
    for _word in input.split_whitespace() {
        count += 1;
    }
    println!("{count}");
}
