//
//  ViewController.h
//  GPTest
//
//  Created by dirlt on 15/12/4.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <Google/SignIn.h>

@interface ViewController : UIViewController<GIDSignInUIDelegate>
@property (nonatomic, weak) IBOutlet GIDSignInButton* signInButton;
@property (nonatomic, weak) IBOutlet UIButton *signOutButton;

@end

