use std::io::Read;
use std::rc::Rc;

fn main() {
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let name = Rc::new(input.trim().to_string());
    let also = Rc::clone(&name);
    println!("{} {}", name, Rc::strong_count(&name));
    let _keep = also;
}
