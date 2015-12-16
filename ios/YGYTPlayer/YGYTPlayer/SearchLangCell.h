//
//  SearchLangCell.h
//  YGYTPlayer
//
//  Created by dirlt on 15/12/9.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface SearchLangCell : UITableViewCell
+ (SearchLangCell*) getInstance;
@property (nonatomic, weak) IBOutlet UISegmentedControl *sc;
- (void) fillLanguages : (NSArray*) languages;
@end
