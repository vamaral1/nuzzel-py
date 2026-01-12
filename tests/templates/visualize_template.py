"""
Template Visualizer

This script generates fake data and renders the email template for visualization.
"""

from pathlib import Path

# Add nuzzel directory to Python path (consistent with nuzzel.main and nuzzel.update_lists)
project_root = Path(__file__).parent.parent.parent

from nuzzel.generators.template_renderer import TemplateRenderer


def generate_fake_data():
    """Generate fake data matching the template expectations."""

    fake_data = {
        'stats': {
            'total_tweets': 127,
            'unique_accounts': 89,
            'total_links': 34
        },
        'themes_summary': {
            'summary': """🔥 **Hot Topics Today:**

The past 24 hours have been marked by significant developments across technology, climate action, remote work, and space exploration. AI and quantum computing continue to dominate discussions, with new breakthroughs and tools emerging that could reshape how we work and create.

**Key Insights:**
- AI adoption is accelerating across creative industries
- Climate tech investments reached record highs this quarter
- Hybrid work models showing 23% productivity improvements""",
            'themes': [
                {
                    'theme': 'AI & Technology',
                    'description': 'Breakthroughs in quantum computing and AI-human collaboration trending',
                    'tweet_ids': ['1600000000000000001', '1600000000000000007']
                },
                {
                    'theme': 'Climate Action',
                    'description': 'New policy announcements and environmental initiatives gaining traction',
                    'tweet_ids': ['1600000000000000002']
                },
                {
                    'theme': 'Space Exploration',
                    'description': 'Exciting developments from SpaceX and NASA missions',
                    'tweet_ids': ['1600000000000000004']
                },
                {
                    'theme': 'Remote Work',
                    'description': 'Continued evolution of distributed team dynamics and productivity tools',
                    'tweet_ids': ['1600000000000000003']
                }
            ]
        },
        'shared_links': {
            'links_by_domain': {
                'techcrunch.com': {
                    'total_shares': 12,
                    'links': [
                        {
                            'link': 'https://techcrunch.com/2024/01/15/openai-gpt-5-timeline/',
                            'title': 'OpenAI announces GPT-5 development timeline',
                            'share_count': 8,
                            'tweets': [
                                {'author_username': '@techguru'},
                                {'author_username': '@ai_expert'},
                                {'author_username': '@futuretech'}
                            ]
                        },
                        {
                            'link': 'https://techcrunch.com/2024/01/14/quantum-breakthrough/',
                            'title': 'Major quantum computing breakthrough achieved',
                            'share_count': 4,
                            'tweets': [
                                {'author_username': '@quantum_phys'},
                                {'author_username': '@tech_news'}
                            ]
                        }
                    ]
                },
                'nytimes.com': {
                    'total_shares': 9,
                    'links': [
                        {
                            'link': 'https://nytimes.com/2024/01/15/climate-policy/',
                            'title': 'New climate policy could transform global emissions targets',
                            'share_count': 6,
                            'tweets': [
                                {'author_username': '@climate_activist'},
                                {'author_username': '@policy_wonk'},
                                {'author_username': '@green_energy'}
                            ]
                        }
                    ]
                },
                'github.com': {
                    'total_shares': 7,
                    'links': [
                        {
                            'link': 'https://github.com/openai/gpt-engineer',
                            'title': 'OpenAI releases GPT-Engineer: AI-powered code generation',
                            'share_count': 7,
                            'tweets': [
                                {'author_username': '@python_dev'},
                                {'author_username': '@ai_coder'},
                                {'author_username': '@tech_startup'}
                            ]
                        }
                    ]
                }
            }
        },
        'top_liked_tweets': [
            {
                'id': '1600000000000000001',
                'text': 'Just discovered an incredible new AI tool that can generate code from natural language descriptions. This is going to revolutionize software development! The future is here. 🤖💻 #AI #Programming',
                'public_metrics': {
                    'like_count': 245,
                    'retweet_count': 67,
                    'reply_count': 23
                },
                'author_username': '@tech_innovator'
            },
            {
                'id': '1600000000000000002',
                'text': 'The climate summit concluded with unprecedented commitments from world leaders. This gives me hope for our planet\'s future. Every action counts! 🌍❤️ #ClimateAction #Hope',
                'public_metrics': {
                    'like_count': 189,
                    'retweet_count': 45,
                    'reply_count': 31
                },
                'author_username': '@climate_scientist'
            },
            {
                'id': '1600000000000000003',
                'text': 'Working remotely has taught me that productivity isn\'t about hours in the office, but about focused work and meaningful connections. The future of work is flexible! 💼🏠',
                'public_metrics': {
                    'like_count': 156,
                    'retweet_count': 38,
                    'reply_count': 19
                },
                'author_username': '@work_culture'
            }
        ],
        'top_retweeted_tweets': [
            {
                'id': '1600000000000000004',
                'text': 'BREAKING: SpaceX successfully launches 23 satellites into orbit. Another step toward global internet coverage. The stars are getting closer! 🚀🌐 #SpaceX #Innovation',
                'public_metrics': {
                    'like_count': 89,
                    'retweet_count': 234,
                    'reply_count': 45
                },
                'author_username': '@space_enthusiast'
            },
            {
                'id': '1600000000000000005',
                'text': 'RT if you agree: The best code is the code that explains itself. Clean, readable, maintainable code > clever tricks every time. What are your coding principles? 💡📝 #Programming #BestPractices',
                'public_metrics': {
                    'like_count': 123,
                    'retweet_count': 198,
                    'reply_count': 67
                },
                'author_username': '@code_master'
            },
            {
                'id': '1600000000000000006',
                'text': 'Exciting news from the research lab! Our team just published findings on sustainable energy storage that could make renewable energy viable 24/7. Science for the win! 🔋⚡ #RenewableEnergy',
                'public_metrics': {
                    'like_count': 145,
                    'retweet_count': 176,
                    'reply_count': 28
                },
                'author_username': '@energy_research'
            }
        ],
        'interest_tweets': {
            'Technology': [
                {
                    'id': '1600000000000000007',
                    'text': 'The convergence of AI and blockchain is creating unprecedented opportunities for decentralized applications. The future of finance and governance is being rewritten! 🔗🤖',
                    'public_metrics': {
                        'like_count': 67,
                        'retweet_count': 23,
                        'reply_count': 12
                    },
                    'author_username': '@blockchain_dev'
                },
                {
                    'id': '1600000000000000008',
                    'text': 'Edge computing is going to be huge. Processing data closer to the source means faster response times and better privacy. The cloud paradigm is shifting! ☁️⚡',
                    'public_metrics': {
                        'like_count': 45,
                        'retweet_count': 18,
                        'reply_count': 9
                    },
                    'author_username': '@cloud_architect'
                }
            ],
            'Science': [
                {
                    'id': '1600000000000000009',
                    'text': 'New CRISPR breakthrough could eliminate genetic diseases before birth. The ethical implications are profound, but the potential to prevent suffering is incredible. 🧬✨',
                    'public_metrics': {
                        'like_count': 89,
                        'retweet_count': 34,
                        'reply_count': 22
                    },
                    'author_username': '@genetic_research'
                }
            ],
            'Business': [
                {
                    'id': '1600000000000000010',
                    'text': 'The gig economy is evolving. Platform cooperativism offers a compelling alternative to the winner-takes-all model. Worker-owned platforms could democratize entrepreneurship! 📈🤝',
                    'public_metrics': {
                        'like_count': 56,
                        'retweet_count': 29,
                        'reply_count': 15
                    },
                    'author_username': '@econ_analyst'
                }
            ]
        },
        'context_categories': {
            'top_categories': [
                {'domain': 'Technology', 'count': 45},
                {'domain': 'Science', 'count': 32},
                {'domain': 'Business', 'count': 28},
                {'domain': 'Climate & Environment', 'count': 22},
                {'domain': 'Space Exploration', 'count': 18},
                {'domain': 'AI & Machine Learning', 'count': 15}
            ]
        },
        'engagement_predictions': {
            'most_likely_to_like': {
                'tweet_id': '1600000000000000001',
                'explanation': 'Based on your history of engaging with AI and technology content, this tweet about AI code generation tools matches your interests perfectly.',
                'tweet': {
                    'id': '1600000000000000001',
                    'text': 'Just discovered an incredible new AI tool that can generate code from natural language descriptions. This is going to revolutionize software development! The future is here. 🤖💻 #AI #Programming',
                    'public_metrics': {
                        'like_count': 245,
                        'retweet_count': 67,
                        'reply_count': 23
                    },
                    'author_username': '@tech_innovator'
                }
            },
            'most_likely_to_retweet': {
                'tweet_id': '1600000000000000004',
                'explanation': 'Your pattern of sharing space exploration and innovation news suggests you\'d likely retweet this SpaceX announcement.',
                'tweet': {
                    'id': '1600000000000000004',
                    'text': 'BREAKING: SpaceX successfully launches 23 satellites into orbit. Another step toward global internet coverage. The stars are getting closer! 🚀🌐 #SpaceX #Innovation',
                    'public_metrics': {
                        'like_count': 89,
                        'retweet_count': 234,
                        'reply_count': 45
                    },
                    'author_username': '@space_enthusiast'
                }
            }
        },
        'list_engagement': {
            'Tech Innovators': {
                'top_liked': [
                    {
                        'id': '1600000000000000011',
                        'text': 'Revolutionary quantum computing breakthrough! We just achieved quantum supremacy in a practical application. The era of quantum computing is finally here. 🧮⚛️ #QuantumComputing #Innovation',
                        'public_metrics': {
                            'like_count': 312,
                            'retweet_count': 89,
                            'reply_count': 45
                        },
                        'author_username': '@quantum_physicist'
                    },
                    {
                        'id': '1600000000000000012',
                        'text': 'Open-source AI just got a massive upgrade. Community-driven development is proving that collaboration beats competition every time. The future belongs to open ecosystems! 🤝🔓 #OpenSource #AI',
                        'public_metrics': {
                            'like_count': 278,
                            'retweet_count': 67,
                            'reply_count': 34
                        },
                        'author_username': '@opensource_dev'
                    }
                ],
                'top_retweeted': [
                    {
                        'id': '1600000000000000013',
                        'text': 'BREAKING: Major tech merger announced today. This combination of AI expertise and quantum capabilities could redefine the industry landscape. Stay tuned for updates! 📈🤝 #TechNews #Mergers',
                        'public_metrics': {
                            'like_count': 156,
                            'retweet_count': 345,
                            'reply_count': 78
                        },
                        'author_username': '@tech_analyst'
                    },
                    {
                        'id': '1600000000000000014',
                        'text': 'The future of coding: AI-assisted development tools that understand context and intent. No more boilerplate code - just pure creativity and problem-solving! 💡🚀 #FutureOfWork #AI',
                        'public_metrics': {
                            'like_count': 189,
                            'retweet_count': 298,
                            'reply_count': 56
                        },
                        'author_username': '@future_coder'
                    }
                ]
            },
            'Climate Action Leaders': {
                'top_liked': [
                    {
                        'id': '1600000000000000015',
                        'text': 'Historic climate agreement signed! World leaders commit to net-zero emissions by 2050. This is the turning point we\'ve been waiting for. Our planet thanks you! 🌍❤️ #ClimateAction #Hope',
                        'public_metrics': {
                            'like_count': 445,
                            'retweet_count': 234,
                            'reply_count': 89
                        },
                        'author_username': '@climate_activist'
                    }
                ],
                'top_retweeted': [
                    {
                        'id': '1600000000000000016',
                        'text': 'Green energy milestone: Solar power now cheaper than coal in 78% of global markets. The renewable revolution is accelerating! ☀️⚡ #RenewableEnergy #ClimateVictory',
                        'public_metrics': {
                            'like_count': 267,
                            'retweet_count': 412,
                            'reply_count': 67
                        },
                        'author_username': '@energy_expert'
                    }
                ]
            }
        }
    }

    return fake_data


def main():
    """Generate and save the rendered template."""
    print("Generating fake data and rendering template...")

    # Generate fake data
    fake_data = generate_fake_data()

    # Create renderer - templates are in the project root, not in tests
    project_root = Path(__file__).parent.parent.parent
    templates_dir = project_root / "templates"
    renderer = TemplateRenderer(str(templates_dir))

    # Render template (using default 1 day for visualization)
    html_content = renderer.render_digest_email(fake_data, time_window_days=1)

    # Save to file
    output_file = Path(__file__).parent / "email_preview.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"Template rendered successfully! Saved to: {output_file}")
    print(f"File size: {len(html_content)} characters")
    print("\nOpen the file in your browser to preview the email template.")


if __name__ == "__main__":
    main()
