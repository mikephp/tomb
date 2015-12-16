//
//  SearchLangCell.m
//  YGYTPlayer
//
//  Created by dirlt on 15/12/9.
//  Copyright © 2015年 dirlt. All rights reserved.
//

#import "SearchLangCell.h"

@implementation SearchLangCell

static SearchLangCell *instance = nil;

+ (SearchLangCell *)getInstance {
    if (instance) return instance;
    NSArray *nibs = [[NSBundle mainBundle] loadNibNamed:@"SearchLangCell" owner:nil options:nil];
    instance = nibs[0];
    return instance;
}

- (void)fillLanguages:(NSArray *)languages {
    [self.sc removeAllSegments];
    [languages enumerateObjectsUsingBlock:^(id  _Nonnull obj, NSUInteger idx, BOOL * _Nonnull stop) {
        [self.sc insertSegmentWithTitle:obj atIndex:idx animated:YES];
    }];
}

- (void)awakeFromNib {
    // Initialization code
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated {
    [super setSelected:selected animated:animated];

    // Configure the view for the selected state
}

@end
