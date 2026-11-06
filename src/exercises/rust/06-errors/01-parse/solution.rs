use std::io::Read;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    match input.trim().parse::<i32>() {
        Ok(n) => println!("{n}"),
        Err(_) => println!("bad"),
    }
}
