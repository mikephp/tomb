//
//  ViewController.m
//  DynamicViewTest
//
//  Created by dirlt on 15/12/13.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "ViewController.h"
#import "DropDownMenuVC.h"

@interface ViewController ()
@property (nonatomic) BOOL show;
@property (nonatomic, strong) DropDownMenuVC* menuVC;
@property (nonatomic, weak) IBOutlet UIButton *clickButton;
@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    self.show = NO;
    self.menuVC = [[DropDownMenuVC alloc] init];
}

- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}

- (IBAction)dropDown:(id)sender {
    if (self.show) {
        self.menuVC.view.hidden = YES;
    } else {
        CGRect buttonPos = self.clickButton.frame;
        self.menuVC.view.frame = CGRectMake(buttonPos.origin.x, buttonPos.origin.y + buttonPos.size.height, 20, 20);
        self.menuVC.view.hidden = NO;
        [self.view addSubview:self.menuVC.view];
    }
    self.show = !self.show;
}

@end
