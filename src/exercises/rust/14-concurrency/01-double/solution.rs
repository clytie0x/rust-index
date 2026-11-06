use std::io::Read;
use std::thread;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let n: i32 = input.trim().parse().unwrap();
    let handle = thread::spawn(move || n * 2);
    let doubled = handle.join().unwrap();
    println!("{doubled}");
}
